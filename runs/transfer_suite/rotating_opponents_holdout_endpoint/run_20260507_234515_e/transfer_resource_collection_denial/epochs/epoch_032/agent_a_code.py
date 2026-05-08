def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obs]

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            # deterministic drift: prefer toward center-ish then toward opponent half
            score = -abs((w - 1) / 2 - nx) - abs((h - 1) / 2 - ny) - 0.01 * md(nx, ny, ox, oy)
            if score == max(-abs((w - 1) / 2 - (sx + mx)) - abs((h - 1) / 2 - (sy + my)) - 0.01 * md(sx + mx, sy + my, ox, oy)
                              for mx, my in moves):
                return [dx, dy]
        return [0, 0]

    # Choose best target resource by maximum current lead (opponent distance - self distance)
    best_target = resources[0]
    best_lead = -10**9
    best_tsd = 10**9
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        lead = od - sd
        if lead > best_lead or (lead == best_lead and sd < best_tsd):
            best_lead, best_tsd, best_target = lead, sd, (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd2 = md(nx, ny, rx, ry)
        od2 = md(ox, oy, rx, ry)
        # primary: keep/improve lead; secondary: reduce own distance; tertiary: avoid moving away globally
        val = (od2 - sd2) * 1000 - sd2 * 10
        # discourage stepping away from any resource when lead is similar (resource_denier style)
        min_self = min(md(nx, ny, rxx, ryy) for (rxx, ryy) in resources)
        min_cur = min(md(sx, sy, rxx, ryy) for (rxx, ryy) in resources)
        val += (min_cur - min_self) * 3
        # deterministic tie-break: prefer smaller dx, then smaller dy
        if val > best_val or (val == best_val and (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1])):
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]