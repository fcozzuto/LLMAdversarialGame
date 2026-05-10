def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    def role_is_purs(role):
        r = (role or "").lower()
        if "purs" in r:
            return True
        if "evad" in r:
            return False
        return None

    sr = role_is_purs(observation.get("self_role"))
    orr = role_is_purs(observation.get("opponent_role"))
    if sr is None:
        sr = (orr is False)
    i_am_pursuer = bool(sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Corner "pull": for pursuer, bias toward reducing opponent-to-corner distance
    closest_corner = min(corners, key=lambda c: d2(ox, oy, c[0], c[1]))

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Obstacle proximity penalty/bonus
        near = 10**9
        for px, py in obs:
            md = abs(nx - px) + abs(ny - py)
            if md < near:
                near = md
        if near == 10**9:
            near = 99

        if i_am_pursuer:
            # Primary: reduce distance to opponent; Secondary: drift toward opponent's corner
            score = d2(nx, ny, ox, oy) + 2 * (10 - min(10, near))
            score += (d2(nx, ny, closest_corner[0], closest_corner[1]) // 8)
            better = (best is None) or (score < best)
        else:
            # Evader: maximize distance from pursuer; avoid obstacles
            score = -d2(nx, ny, ox, oy) - (2 * (10 - min(10, near)))
            score -= (d2(nx, ny, closest_corner[0], closest_corner[1]) // 16)
            better = (best is None) or (score > best)

        if better:
            best = score
            best_move = [dx, dy]

    return best_move