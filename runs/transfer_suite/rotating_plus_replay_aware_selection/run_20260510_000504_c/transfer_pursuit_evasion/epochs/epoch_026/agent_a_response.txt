def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    opp_is_evader = ("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role)
    i_am_evader = self_is_evader or (not opp_is_evader)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if valid(x + dx, y + dy):
                c += 1
        return c

    def center_score(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny)
        m = mobility(nx, ny)
        c = center_score(nx, ny)

        # Pursuer: minimize distance; Evader: maximize distance.
        if i_am_evader:
            score = d + 0.7 * m + 0.05 * c
        else:
            score = -d + 0.7 * m + 0.05 * c

        # Deterministic tie-breakers: prefer higher mobility then higher center then lexicographic move.
        if best_score is None:
            best_score = score
            best_move = (dx, dy)
        else:
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
            elif score == best_score:
                tb_m = mobility(sx + best_move[0], sy + best_move[1])
                if m > tb_m:
                    best_move = (dx, dy)
                elif m == tb_m:
                    tb_c = center_score(sx + best_move[0], sy + best_move[1])
                    if c > tb_c or (c == tb_c and (dx, dy) > best_move):
                        best_move = (dx, dy)

    return [best_move[0], best_move[1]]