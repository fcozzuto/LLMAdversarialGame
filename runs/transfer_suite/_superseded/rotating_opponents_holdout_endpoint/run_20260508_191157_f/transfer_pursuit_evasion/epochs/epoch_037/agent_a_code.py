def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer")

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer staying put vs moving lexicographically deterministically
    deltas.sort(key=lambda t: (abs(t[0]) + abs(t[1]) != 0, t[0], t[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                c += 1
        return c

    def obs_prox(x, y):
        if not obs_set:
            return 99
        best = 10**9
        for ax, ay in obs_set:
            d = abs(ax - x) + abs(ay - y)
            if d < best:
                best = d
                if best <= 1:
                    break
        return best

    # Baseline target corner for evasion: farthest corner from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        d_to_opp = man(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        prox = obs_prox(nx, ny)
        d_to_corner = man(nx, ny, far_corner[0], far_corner[1])

        if role == "pursuer":
            key = (d_to_opp, -mob, -prox, d_to_corner, dx, dy)
        else:  # evader
            key = (-d_to_opp, mob, -prox, -d_to_corner, dx, dy)

        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]