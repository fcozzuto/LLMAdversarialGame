def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    self_count = int(observation.get("self_territory_count") or len(self_terr))
    opp_count = int(observation.get("opponent_territory_count") or len(opp_terr))
    behind = 1 if self_count < opp_count else 0

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    candidates = [(dx, dy) for dx in dxs for dy in dys if not (dx == 0 and dy == 0 and False)]
    # Deterministic tie-break order: prefer toward center then toward NW-ish
    candidates.sort(key=lambda t: (t[0], t[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        cell = (nx, ny)
        is_ours = cell in self_terr
        is_opp = cell in opp_terr
        is_un = cell in unclaimed

        # Encourage expansion to center, keep distance from opponent unless we need flips.
        score = 0.0
        score += -3.2 * d_center
        score += 1.1 * d_opp

        if is_ours:
            score += 0.6
        elif is_un:
            score += 2.2
        elif is_opp:
            if behind:
                score += 4.0 + 0.1 * d_opp
            else:
                score -= 3.5 + 0.1 * d_opp

        # Discourage stepping into opponent territory too close to our current position.
        score += -0.4 * (abs(nx - sx) + abs(ny - sy))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: smaller |dx|+|dy| then lexicographic
            if abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1]) or (
                abs(dx) + abs(dy) == abs(best_move[0]) + abs(best_move[1]) and (dx, dy) < best_move
            ):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]