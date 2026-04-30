def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = dist(rx, ry, nx, ny)
                if d < dmin:
                    dmin = d
            near_opp = 0
            if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
                near_opp = 3
            score = (dmin + near_opp, abs(nx - ox) + abs(ny - oy), dx, dy)
        else:
            cx, cy = (W - 1) // 2, (H - 1) // 2
            away = abs(nx - ox) + abs(ny - oy)
            toward = dist(cx, cy, nx, ny)
            score = (toward - 0.2 * away, -away, dx, dy)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]
    return best[1]