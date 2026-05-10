def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("escape" in r)

    i_evader = is_evader(observation.get("self_role"))
    opp_evader = is_evader(observation.get("opponent_role"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors_free_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def opponent_best_move(myx, myy):
        # Opponent moves to optimize their objective deterministically.
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                nx, ny = ox, oy
            d = dist(myx, myy, nx, ny)
            nf = neighbors_free_count(nx, ny)
            # Evader: maximize distance and mobility; Pursuer: minimize distance and prefer low mobility for evader.
            val = d * (10 if opp_evader else -10) + (nf if opp_evader else -nf)
            if best_val is None or (val > best_val if opp_evader else val < best_val):
                best_val = val
                best = (nx, ny)
        return best

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        # One-step lookahead: opponent responds.
        enx, eny = opponent_best_move(nx, ny)
        capture = (nx == enx and ny == eny)
        d_after = dist(nx, ny, enx, eny)
        nf = neighbors_free_count(nx, ny)

        # If capture happens, it's bad for evader and great for pursuer.
        if capture:
            val = -10**9 if i_evader else 10**9
        else:
            # Evader: maximize distance, avoid being trapped (low mobility).
            # Pursuer: minimize distance, prefer states that reduce opponent mobility.
            opp_mob = neighbors_free_count(enx, eny)
            if i_evader:
                val = d_after * 20 + nf * 2 - opp_mob
            else:
                val = -d_after * 20 - (opp_mob * 2) + nf
        candidates.append((val, dx, dy, nx, ny))

    candidates.sort(key=lambda t: (-t[0], t[1], t[2])) if i_evader else candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]