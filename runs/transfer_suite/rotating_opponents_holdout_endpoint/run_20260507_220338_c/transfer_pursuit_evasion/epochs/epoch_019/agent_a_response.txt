def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_pursuer_step(pox, poy, tx, ty):
        best = None
        bestd = None
        for dx, dy in dirs:
            nx, ny = pox + dx, poy + dy
            if not in_bounds(nx, ny) or (nx, ny) in blocked:
                continue
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    best_val = None

    if role == "evader":
        # Evader: maximize distance after predicting pursuer response; also avoid getting too close now.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in blocked:
                continue
            pdx, pdy = best_pursuer_step(ox, oy, nx, ny)
            nex, ney = ox + pdx, oy + pdy
            d_after = (nex - nx) * (nex - nx) + (ney - ny) * (ney - ny)
            d_now = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            val = d_after + 0.15 * d_now
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # Pursuer: greedily minimize distance to evader; slight bias to stay away from obstacles.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in blocked:
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            obs_near = 0
            for ax, ay in dirs:
                px, py = nx + ax, ny + ay
                if in_bounds(px, py) and (px, py) in blocked:
                    obs_near += 1
            val = -d - 0.05 * obs_near
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]