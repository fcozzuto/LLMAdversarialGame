def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def blocked(nx, ny):
        return (nx, ny) in obs or not (0 <= nx < w and 0 <= ny < h)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        selfd = man((nx, ny), (ox, oy))
        best_adv = -10**9
        closest_res = 10**9
        row_align = abs(oy - ny)

        for r in resources:
            sd = abs(r[0] - nx) + abs(r[1] - ny)
            od = abs(r[0] - ox) + abs(r[1] - oy)
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
            if sd < closest_res:
                closest_res = sd

        # Prefer outperforming opponent on some resource, keep distance, and align to opponent's sweep row
        val = 2.4 * best_adv + 0.12 * selfd - 0.10 * closest_res - 0.25 * row_align
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]