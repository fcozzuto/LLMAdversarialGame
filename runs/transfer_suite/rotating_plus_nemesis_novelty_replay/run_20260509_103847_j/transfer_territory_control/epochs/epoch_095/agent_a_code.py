def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    rx, ry = None, None
    bestd = 10**9
    for x, y in resources:
        d = abs(x - sx) + abs(y - sy)
        if d < bestd:
            bestd, rx, ry = d, x, y

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if rx is not None:
            dist_to_res = abs(nx - rx) + abs(ny - ry)
            res_here = 1 if (nx, ny) in set(resources) else 0
            dist_to_opp = abs(nx - ox) + abs(ny - oy)
            score = 1000 * res_here - 5 * dist_to_res + 0.5 * dist_to_opp
        else:
            dist_to_opp = abs(nx - ox) + abs(ny - oy)
            score = 5 * dist_to_opp

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]