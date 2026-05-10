def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for k in ("resources", "unclaimed_cells"):
        if len(targets) == 0 and observation.get(k) is not None:
            for p in observation.get(k) or []:
                if p and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                        targets.append((x, y))
            if targets:
                break

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, -10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if targets:
            md = 10**9
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if d < md:
                    md = d
            near_score = -md
        else:
            cx, cy = w // 2, h // 2
            near_score = - (abs(cx - nx) + abs(cy - ny))
        opp_penalty = abs(ox - nx) + abs(oy - ny)
        cand = ( -near_score, -opp_penalty, -dx, -dy )
        if cand < best[:4] + (0,):
            best = (cand[0], cand[1], dx, dy)

    return [int(best[2]), int(best[3])]