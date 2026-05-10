def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_evade = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    if not ("purs" in self_role or "chase" in self_role):
        if ("purs" in opp_role) or ("chase" in opp_role):
            i_evade = True
        elif ("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role):
            i_evade = False

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = d2 if i_evade else -d2

        # small tie-break: prefer not moving into tight obstacle vicinity
        tight = 0
        for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ax, ay = nx + adx, ny + ady
            if not inb(ax, ay):
                tight += 1
        val -= tight * (1 if i_evade else 0)

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]