def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not res:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_adv = None
        best_selfd = None
        best_rx = best_ry = 0

        for r in res:
            rx, ry = r[0], r[1]
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            adv = opp_d - self_d  # positive means we are closer than opponent
            if best_adv is None or adv > best_adv or (adv == best_adv and (self_d < best_selfd or (self_d == best_selfd and (rx, ry) < (best_rx, best_ry)))):
                best_adv = adv
                best_selfd = self_d
                best_rx, best_ry = rx, ry

        # Prefer moves that maximize ability to beat opponent to some resource.
        key = (-best_adv, best_selfd, best_rx, best_ry)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move