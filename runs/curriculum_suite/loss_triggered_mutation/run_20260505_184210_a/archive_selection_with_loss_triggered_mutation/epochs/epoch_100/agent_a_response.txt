def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (d[0], d[1]))  # deterministic tie-breaker

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate best attainable "lead" against opponent over remaining resources (one-step lookahead)
        if resources:
            best_lead = -10**9
            best_self = 10**9
            best_opp = 10**9
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                lead = od - sd  # positive means we're closer
                if lead > best_lead or (lead == best_lead and sd < best_self) or (lead == best_lead and sd == best_self and od < best_opp):
                    best_lead = lead
                    best_self = sd
                    best_opp = od
            # Additional pressure: prefer reducing distance to opponent when already ahead (interception vibe)
            opp_near_bonus = -man(nx, ny, ox, oy)
            value = (best_lead, -best_self, opp_near_bonus)
        else:
            # No visible resources: move to maximize distance from opponent (defensive) while not uselessly stuck
            value = (-man(nx, ny, ox, oy), -man(nx, ny, sx, sy))
        if best is None or value > best[0]:
            best = (value, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]