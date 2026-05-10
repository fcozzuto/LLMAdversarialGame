def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    x0, y0 = self_pos
    x1, y1 = opp_pos
    obs_set = set((ox, oy) for ox, oy in obstacles)

    sr = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursur" in sr) or ("chaser" in sr) or ("hunter" in sr)
    is_evader = ("evad" in sr) or ("runner" in sr) or ("escape" in sr)

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    best = None
    best_val = None

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # If role string is unclear, act like pursuer (generally safe for scoring).
    pursuer_mode = is_pursuer or (not is_evader)

    for dx in dxs:
        for dy in dys:
            nx, ny = x0 + dx, y0 + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            d2 = dist2(nx, ny, x1, y1)
            # Capture ends game at equal position (radius 0). Prefer it decisively.
            cap = 1 if (nx == x1 and ny == y1) else 0

            # Obstacle proximity penalty: slightly discourage moving adjacent to obstacles.
            prox = 0
            for ox, oy in obs_set:
                if abs(nx - ox) <= 1 and abs(ny - oy) <= 1 and (nx != ox or ny != oy):
                    prox += 1

            val = (-10**6) if cap else 0
            if pursuer_mode:
                # Maximize value -> smaller distance is better; capture already handled.
                val += -d2 - 0.3 * prox
            else:
                # Evader wants to maximize distance from pursuer.
                val += d2 - 0.3 * prox

            if best is None or val > best_val:
                best_val = val
                best = [dx, dy]

    return best if best is not None else [0, 0]