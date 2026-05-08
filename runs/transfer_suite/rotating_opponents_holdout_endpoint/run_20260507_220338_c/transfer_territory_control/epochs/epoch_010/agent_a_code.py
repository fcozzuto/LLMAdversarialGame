def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not inb(sx, sy):
        return [0, 0]

    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    # Pick a deterministic target: prefer capturing near opponent, else claim near center/unclaimed.
    tx = ty = None
    if opp_terr:
        # If we can step into/near opponent, do that: choose closest opponent cell.
        best = None
        bestd = 10**9
        for ox, oy in list(opp_terr)[:48]:
            d = (ox - sx) * (ox - sx) + (oy - sy) * (oy - sy)
            if d < bestd or (d == bestd and (oy, ox) < (best[1], best[0]) if best else True):
                bestd = d
                best = (ox, oy)
        tx, ty = best
    if tx is None or (observation.get("unclaimed_cells") is not None and observation.get("unclaimed_cells") != [] and len(self_terr) < len(opp_terr) and len(unclaimed) > 0):
        # Claim: nearest unclaimed; if none, drift to center.
        if unclaimed:
            best = None
            bestd = 10**9
            for ux, uy in list(unclaimed)[:64]:
                d = (ux - sx) * (ux - sx) + (uy - sy) * (uy - sy)
                if d < bestd or (d == bestd and (uy, ux) < (best[1], best[0]) if best else True):
                    bestd = d
                    best = (ux, uy)
            tx, ty = best
        else:
            tx, ty = (w // 2, h // 2)

    # Move greedily among legal deltas, with tie-break toward expanding (closer to target, then toward border).
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestscore = 10**18
    opp = opp_terr
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Base: distance to target.
        dist = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # Bonus for stepping into opponent territory (flipping enabled).
        flip_bonus = -100000 if (nx, ny) in opp else 0
        # Small preference to borders/frontiers: proximity to opponent.
        border = 0
        if opp:
            md = 10**9
            for ox, oy in list(opp)[:24]:
                dd = abs(nx - ox) + abs(ny - oy)
                if dd < md:
                    md = dd
            border = -10 * md
        # Discourage staying still if alternatives exist.
        stay_pen = 5 if (dx, dy) == (0, 0) else 0
        score = dist + stay_pen + flip_bonus + border
        if score < bestscore or (score == bestscore and (dx, dy) < bestm):
            bestscore = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]