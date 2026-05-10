def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to_opp(x, y):
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                return True
        return False

    def pick_target():
        if opp_terr and unclaimed:
            best = None
            for (x, y) in unclaimed:
                if adj_to_opp(x, y):
                    d = max(abs(x - sx), abs(y - sy))
                    t = (d, y, x)
                    if best is None or t < best[0]:
                        best = (t, (x, y))
            if best is not None:
                return best[1]
        if unclaimed:
            # If no direct frontier, head toward unclaimed closer to opponent center.
            if opp_terr:
                cx = sum(x for x, y in opp_terr) / len(opp_terr)
                cy = sum(y for x, y in opp_terr) / len(opp_terr)
                best = None
                for (x, y) in unclaimed:
                    d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                    t = (d, y, x)
                    if best is None or t < best[0]:
                        best = (t, (x, y))
                return best[1]
            # Fallback: closest unclaimed to us
            return min(unclaimed, key=lambda p: (max(abs(p[0] - sx), abs(p[1] - sy)), p[1], p[0]))
        return (ox, oy)

    tx, ty = pick_target()

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_terr:
            score += 2
            if adj_to_opp(nx, ny):
                score += 2
        elif (nx, ny) in opp_terr:
            score += 10
            if adj_to_opp(nx, ny):
                score += 3
        elif (nx, ny) in unclaimed:
            score += 5 if adj_to_opp(nx, ny) else 1

        # Distance shaping toward target
        score += 6 - 2 * max(abs(nx - tx), abs(ny - ty))

        # Slightly avoid moving away from opponent territory when possible
        if opp_terr:
            score += 0.5 if adj_to_opp(nx, ny) else 0

        # Deterministic tie-break
        if score > best_score or (score == best_score and (dy, dx) < (best_move[1], best_move[0])):
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # If all moves blocked/unavailable, stay.
        return [0, 0]
    return best_move