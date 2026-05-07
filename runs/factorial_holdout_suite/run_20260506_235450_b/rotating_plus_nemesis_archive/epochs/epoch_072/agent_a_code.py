def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obs.add((px, py))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = -10**18
    best_move = [0, 0]

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        if not res:
            # Move toward center while staying away from opponent
            dcent = abs(nx - center_x) + abs(ny - center_y)
            dstop = dist((nx, ny), (ox, oy))
            score = -dcent + 0.15 * dstop
        else:
            score = -0.01 * (abs(dx) + abs(dy))
            # Race for resources: prefer cells that can reach a resource before opponent
            for rx, ry in res:
                my_d = dist((nx, ny), (rx, ry))
                op_d = dist((ox, oy), (rx, ry))
                if my_d == 0:
                    score += 1e9
                else:
                    if my_d < op_d:
                        score += 2000 - 40 * my_d
                    elif my_d == op_d:
                        score += 50 - 5 * my_d
                    else:
                        score -= 120 + 25 * (my_d - op_d)
                # Mild preference for being closer once race condition is favorable
                score += -0.8 * my_d
                # Avoid handing the opponent an immediate capture nearby
                score += -0.03 * dist((nx, ny), (ox, oy))
        if score > best or (score == best and [dx, dy] < best_move):
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]