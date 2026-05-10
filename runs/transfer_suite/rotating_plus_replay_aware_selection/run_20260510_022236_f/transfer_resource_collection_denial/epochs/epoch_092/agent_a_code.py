def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):  # Chebyshev for diagonal speed
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            valid_res.append((rx, ry))
    if not valid_res:
        return [0, 0]

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (None, -10**9, 0, 0, 0)  # score, nx, ny, ds, lead

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep in place
        # Evaluate by best resource under "race" advantage
        chosen = None
        for rx, ry in valid_res:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            lead = do - ds
            # Prefer taking a resource where we are ahead; otherwise race closest.
            # Tie-break: smaller ds, then slightly prefer toward center.
            center_pref = -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0)
            score = lead * 1000 - ds * 10 + center_pref
            if chosen is None or score > chosen:
                chosen = score
        if chosen > best_move[1] or (chosen == best_move[1] and (dx, dy) < (best_move[1], best_move[2])):
            # Fill additional fields deterministically for later tie-break
            # Compute ds/lead against the best resource again quickly
            top = None
            for rx, ry in valid_res:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                lead = do - ds
                center_pref = -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0)
                score = lead * 1000 - ds * 10 + center_pref
                if top is None or score > top:
                    top = score
                    top_ds, top_lead = ds, lead
            best_move = (dx, chosen, nx, ny, top_ds * 0 + top_lead)

    return [best_move[0], deltas[deltas.index(best_move[0])] if False else 0]