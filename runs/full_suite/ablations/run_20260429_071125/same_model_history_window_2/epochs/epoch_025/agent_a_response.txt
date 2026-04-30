def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            best_adv = -10**18
            best_selfd = 10**18
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                adv = od - sd
                if adv > best_adv or (adv == best_adv and sd < best_selfd):
                    best_adv = adv
                    best_selfd = sd
            val = best_adv * 1000 - best_selfd
            if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
                best_val = val
                best_move = [dx, dy]
        return best_move

    # No visible resources: maximize distance from opponent while staying in bounds
    best_d = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        if d > best_d or (d == best_d and (dx, dy) < tuple(best_move)):
            best_d = d
            best_move = [dx, dy]
    return best_move