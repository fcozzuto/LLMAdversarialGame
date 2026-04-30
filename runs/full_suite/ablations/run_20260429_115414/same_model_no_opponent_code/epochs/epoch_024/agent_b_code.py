def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = observation.get("resources") or []
    res = [(int(r[0]), int(r[1])) for r in resources if len(r) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    if res:
        best_resource = min(res, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        rx, ry = best_resource
        def score(move):
            dx, dy = move
            nx, ny = sx + dx, sy + dy
            d = abs(rx - nx) + abs(ry - ny)
            do = abs(ox - nx) + abs(oy - ny)
            return (d, -do, dx, dy)
        move = sorted(candidates, key=score)[0]
        return [int(move[0]), int(move[1])]

    cx, cy = w // 2, h // 2
    def score_fallback(move):
        dx, dy = move
        nx, ny = sx + dx, sy + dy
        dc = abs(cx - nx) + abs(cy - ny)
        do = abs(ox - nx) + abs(oy - ny)
        return (dc, -do, dx, dy)
    move = sorted(candidates, key=score_fallback)[0]
    return [int(move[0]), int(move[1])]