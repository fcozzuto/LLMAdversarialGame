def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    self_role = observation.get("self_role", "pursuer") or "pursuer"
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    free = [c for c in corners if c not in obstacles] or corners
    if "evader" in self_role:
        target = max(free, key=lambda c: cheb(c[0], c[1], ox, oy))
        want = "maximize"
    else:
        target = min(free, key=lambda c: cheb(c[0], c[1], ox, oy))
        want = "minimize"

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_tgt = cheb(nx, ny, target[0], target[1])
        if want == "maximize":
            val = (d_opp, -d_tgt)
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best)
        else:
            val = (-d_opp, d_tgt)
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best)
        if better:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]