def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_val = -10**18
    best_move = (0, 0)

    opp_pos = (ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_sep_opp = man(nx, ny, opp_pos[0], opp_pos[1])
        on_res = 1 if (nx, ny) in set(resources) else 0

        best_adv = -10**9
        best_my_dist = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            oppd = man(opp_pos[0], opp_pos[1], rx, ry)
            adv = oppd - myd
            if adv > best_adv:
                best_adv = adv
            if myd < best_my_dist:
                best_my_dist = myd

        # Prefer winning races to resources; keep separation from opponent to avoid being trapped.
        val = 5.0 * best_adv - 1.0 * best_my_dist - 0.15 / (1 + my_sep_opp) + 20.0 * on_res
        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]