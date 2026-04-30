def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def nearest_after(nx, ny):
        if not resources:
            return d2(nx, ny, w - 1, h - 1)
        best = None
        for rx, ry in resources:
            dd = d2(nx, ny, rx, ry)
            if best is None or dd < best:
                best = dd
        return best

    # Deterministic tie-break ordering depends on computed score then move index
    best_move = (0, 0)
    best_score = None

    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Primary: reduce distance to nearest resource
        nf = nearest_after(nx, ny)
        # Secondary: keep distance from opponent (more important when opponent is near)
        no = d2(nx, ny, ox, oy)
        opp_near = d2(sx, sy, ox, oy) <= 4  # within 2 steps (chebyshev-ish proxy via d2)
        # Higher score is better
        score = (-nf) + (0.35 if opp_near else 0.15) * no
        # Tiny bias to break ties deterministically (prefer staying still slightly)
        score += -0.001 * (abs(dx) + abs(dy)) + (0.0005 if dx == 0 and dy == 0 else 0.0)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]