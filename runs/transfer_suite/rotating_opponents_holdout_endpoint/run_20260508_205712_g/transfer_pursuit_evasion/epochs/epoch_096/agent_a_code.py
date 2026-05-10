def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    orr = str(observation.get("opponent_role") or "").lower()
    self_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("hunter" in sr)
    opp_pursuer = ("pursuer" in orr) or ("chaser" in orr) or ("hunter" in orr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid_next_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((nx, ny, dx, dy))
        if not out:
            out = [(x, y, 0, 0)]
        return out

    self_choices = valid_next_from(sx, sy)

    # If we are pursuer: maximize capture likelihood by minimizing distance after opponent response.
    # If we are evader: maximize distance after opponent response.
    best = None
    best_val = None
    for nx, ny, sdx, sdy in self_choices:
        opp_choices = valid_next_from(ox, oy)
        best_opp = None
        best_opp_val = None
        for pax, pay, odx, ody in opp_choices:
            d = dist2(nx, ny, pax, pay)
            # Opponent pursuer minimizes our distance; opponent evader maximizes it.
            val = -d if opp_pursuer else d
            if best_opp is None:
                best_opp = (pax, pay, odx, ody)
                best_opp_val = val
            else:
                if val > best_opp_val:
                    best_opp_val = val
                    best_opp = (pax, pay, odx, ody)
        # Now evaluate our objective against their best response.
        d_after = dist2(nx, ny, best_opp[0], best_opp[1])
        val_self = -d_after if self_pursuer else d_after
        if best is None:
            best = (sdx, sdy)
            best_val = val_self
        else:
            if val_self > best_val:
                best_val = val_self
                best = (sdx, sdy)

    return [int(best[0]), int(best[1])]