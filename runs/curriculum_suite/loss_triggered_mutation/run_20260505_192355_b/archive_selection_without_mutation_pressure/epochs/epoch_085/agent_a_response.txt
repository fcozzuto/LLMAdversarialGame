def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        valid = (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles)
        if not valid:
            continue  # keep out of obstacle/bounds by not choosing it

        best_res_val = -10**18
        best_self_dist = 10**9
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                best_res_val = 10**12
                best_self_dist = 0
                break
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            res_val = opp_d - self_d  # higher means we are closer than opponent
            if res_val > best_res_val or (res_val == best_res_val and self_d < best_self_dist):
                best_res_val = res_val
                best_self_dist = self_d

        # Favor winning a contested resource; break ties by going closer to it.
        score = best_res_val * 1000 - best_self_dist
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]