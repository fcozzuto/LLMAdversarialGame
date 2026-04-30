def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if len(moves) != 9:
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    neigh_obs = set()
    for (x, y) in obstacles:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    neigh_obs.add((nx, ny))

    turn = int(observation.get("turn_index", 0) or 0)
    prefer_left_half = ((turn % 2) == 0)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_res_d = 10**9
        best_res = None
        if resources:
            for rx, ry in resources:
                d = md(nx, ny, rx, ry)
                # Small deterministic bias: prefer resources on our "half"
                if prefer_left_half:
                    side_bias = 0 if rx < w // 2 else 2
                else:
                    side_bias = 0 if rx >= w // 2 else 2
                d2 = d + side_bias
                if d2 < best_res_d or (d2 == best_res_d and (rx, ry) < best_res):
                    best_res_d = d2
                    best_res = (rx, ry)
        else:
            best_res_d = md(nx, ny, ox, oy)

        opp_d = md(nx, ny, ox, oy)
        center_bias = -abs((nx - (w - 1) / 2)) - abs((ny - (h - 1) / 2))
        obstacle_risk = 2 if (nx, ny) in neigh_obs else 0

        # Prefer getting closer to resources, staying away from opponent, and avoiding obstacle-adjacent cells.
        score = (-best_res_d) + (0.25 * opp_d) + (0.05 * center_bias) - obstacle_risk
        candidates.append((score, dx, dy, best_res))

    if not candidates:
        return [0, 0]

    # Deterministic tie-break: higher score, then smaller dx, then smaller dy, then lexicographic resource.
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3] if t[3] is not None else (999, 999)))
    _, dx, dy, _ = candidates[0]
    return [int(dx), int(dy)]