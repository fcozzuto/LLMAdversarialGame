def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    # Opponent position helps break ties deterministically
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    # If opponent territory is empty, expand into unclaimed; otherwise, contest by entering opponent territory.
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if (nx, ny) in opp_terr:
            val = 2000
            # Prefer pushes that also reduce distance to opponent position (deterministic pressure)
            val -= (abs(nx - ox) + abs(ny - oy))
            # Prefer moves that are not immediately adjacent to obstacles (light safety)
            val -= sum((nx + ax, ny + ay) in blocks for ax in (-1, 0, 1) for ay in (-1, 0, 1))
        elif (nx, ny) in unclaimed:
            # Claim frontier: closer to opponent position is usually better
            val = 650 - (abs(nx - ox) + abs(ny - oy))
            # If unclaimed is adjacent to opponent territory, boost
            val += 120 * any((nx + ax, ny + ay) in opp_terr for ax, ay in dirs)
        elif (nx, ny) in self_terr:
            # Defensive hold if nothing else
            val = 120 - (abs(nx - ox) + abs(ny - oy))
        else:
            # Neutral empty/non-relevant cell
            val = 30 - (abs(nx - ox) + abs(ny - oy))

        # Deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]