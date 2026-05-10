def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def is_evader(role):
        r = str(role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("escape" in r)

    self_evader = is_evader(observation.get("self_role", ""))
    opp_evader = is_evader(observation.get("opponent_role", ""))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(px, py):
        out = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if ok(nx, ny):
                out.append((dx, dy, nx, ny))
        return out

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    my_legals = legal(sx, sy)
    if not my_legals:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx0, dy0, nx0, ny0 in my_legals:
        # Opponent greedy 1-step response to our resulting position
        opp_legals = legal(ox, oy)
        if not opp_legals:
            d_after = dist2(nx0, ny0, ox, oy)
        else:
            best_opp = None
            best_opp_val = None
            for dox, doy, nox, noy in opp_legals:
                d = dist2(nox, noy, nx0, ny0)
                val = d if opp_evader else -d
                if best_opp is None or val > best_opp_val or (val == best_opp_val and (dox, doy) < best_opp):
                    best_opp = (dox, doy)
                    best_opp_val = val
            nox, noy = ox + best_opp[0], oy + best_opp[1]
            d_after = dist2(nx0, ny0, nox, noy)

        my_val = -d_after if self_evader is False else d_after
        if best_val is None or my_val > best_val or (my_val == best_val and (dx0, dy0) < best_move):
            best_val = my_val
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]