def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("evader" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def prox_to_obstacle(x, y):
        m = 10**9
        for a, b in obstacles:
            d = abs(x - a) + abs(y - b)
            if d < m:
                m = d
                if m == 0:
                    return 0
        return 0 if m == 10**9 else m

    best = (None, -10**18 if is_evader else 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        p = prox_to_obstacle(nx, ny)
        # evader: maximize distance to opponent + avoid obstacles; also bias toward farthest corner
        if is_evader:
            far_corner = max(abs(c[0] - ox) + abs(c[1] - oy) for c in corners)
            corner_dist = max(abs(c[0] - nx) + abs(c[1] - ny) for c in corners)
            score = (d_opp * 10) + (corner_dist * 2) + (p) - (far_corner * 0.001)
            if score > best[1]:
                best = ((dx, dy), score)
        else:
            # pursuer: minimize distance to opponent; prefer safer tiles
            score = (d_opp * 10) - (p)
            if score < best[1]:
                best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]