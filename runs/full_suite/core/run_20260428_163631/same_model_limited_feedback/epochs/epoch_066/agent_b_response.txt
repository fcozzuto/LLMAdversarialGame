def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    def best_target():
        if not resources:
            return (w//2, h//2), True
        best = None
        best_key = None
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            myd = dist2((sx, sy), (rx, ry))
            opd = dist2((ox, oy), (rx, ry))
            # Prefer closer resources, and avoid targets the opponent is closer to
            key = (myd - 0.6*opd, myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return (best if best is not None else (w//2, h//2)), (best is None)

    target, _ = best_target()

    # If currently on target, head to next best by same heuristic
    if (sx, sy) == target and resources:
        for r in resources:
            if tuple(r) == target or tuple(r) in obstacles:
                continue
            target = (r[0], r[1])
            break

    tx, ty = target
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Score for moving to (nx, ny): closer to target, and not giving opponent an immediate capture
        d_to_t = (nx - tx)*(nx - tx) + (ny - ty)*(ny - ty)
        # Avoid stepping into a cell adjacent to an opponent-leaning path by penalizing closeness between agents
        between = dist2((nx, ny), (ox, oy))
        opp_next = (clamp(ox + (1 if ox < nx else (-1 if ox > nx else 0)), 0, w-1),
                    clamp(oy + (1 if oy < ny else (-1 if oy > ny else 0)), 0, h-1))
        oppd = dist2(opp_next, (tx, ty))
        # If the target is exactly on a resource, being there is great; otherwise, just approach
        on_resource = 1 if any((r[0] == nx and r[1] == ny) for r in resources) else 0
        score = -d_to_t + 0.08*between - 0.5*oppd + 3.0*on_resource
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all legal moves invalid (rare), stay
    return [int(best_move[0]), int(best_move[1])]