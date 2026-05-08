def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = dirs[0]
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp_before = man(sx, sy, ox, oy)
        d_opp_after = man(nx, ny, ox, oy)
        opp_gain = d_opp_before - d_opp_after

        res_gain = 0
        if resources:
            d_res_before = min(man(sx, sy, rx, ry) for rx, ry in resources)
            d_res_after = min(man(nx, ny, rx, ry) for rx, ry in resources)
            res_gain = d_res_before - d_res_after

        score = opp_gain * 10 + res_gain * 3
        if (nx, ny) == (ox, oy):
            score += 100

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]