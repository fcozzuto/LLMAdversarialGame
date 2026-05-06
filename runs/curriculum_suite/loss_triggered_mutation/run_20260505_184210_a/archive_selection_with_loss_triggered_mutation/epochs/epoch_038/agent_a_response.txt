def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Small deterministic priority ordering when scores tie
    move_rank = {m: i for i, m in enumerate(moves)}

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate by best advantage over remaining resources
        # advantage = (opponent distance - our distance); larger is better.
        best_adv = -10**18
        best_our = 10**9
        best_r = None
        for (rx, ry) in resources:
            our_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            adv = opp_d - our_d
            if adv > best_adv or (adv == best_adv and our_d < best_our) or (adv == best_adv and our_d == best_our and (best_r is None or (rx, ry) < best_r)):
                best_adv = adv
                best_our = our_d
                best_r = (rx, ry)

        # If we can step onto a resource, make it dominant.
        on_resource = 1 if best_r is not None and (best_r[0] == nx and best_r[1] == ny) else 0

        # Additionally prefer moves that increase our advantage spread (robustness).
        # Use second-best advantage proxy via minimum (our_d - opp_d) across resources not equal to best_r.
        worst_def = 10**9
        for (rx, ry) in resources:
            if best_r is not None and rx == best_r[0] and ry == best_r[1]:
                continue
            our_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # lower is better for opponent; we want to keep our_d smaller than opp_d
            worst_def = min(worst_def, our_d - opp_d)

        val = (on_resource * 10**6) + best_adv * 1000 - best_our + worst_def
        if val > best_val or (val == best_val and move_rank[(dx, dy)] < move_rank[best]):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]