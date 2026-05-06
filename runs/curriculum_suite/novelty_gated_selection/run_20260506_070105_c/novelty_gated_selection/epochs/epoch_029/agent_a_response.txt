def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx, dy = x - cx, y - cy
        return - (dx * dx + dy * dy)

    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if not resources:
            key = (-(center_bias(nx, ny)), 0, 0, dx, dy)
        else:
            best_res = None
            for rx, ry in resources:
                my_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)
                # Race win: prioritize moves that reduce our distance while exploiting opponent lead/lag
                # Also add a mild preference to approach resources closer immediately.
                race = (opp_d - my_d) * 4 - my_d
                # If we are behind on that resource, still allow blocking by moving toward it.
                lead_term = 0
                if opp_d <= my_d:
                    lead_term = (my_d - opp_d) * 1.5
                sc = race - lead_term
                if best_res is None or sc > best_res[0]:
                    best_res = (sc, my_d, opp_d, rx, ry)
            sc, my_d, opp_d, rx, ry = best_res
            # Tie-break: prefer closer immediate resource, then maximize race, then center bias
            key = (-sc, my_d, -opp_d, -center_bias(nx, ny), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]