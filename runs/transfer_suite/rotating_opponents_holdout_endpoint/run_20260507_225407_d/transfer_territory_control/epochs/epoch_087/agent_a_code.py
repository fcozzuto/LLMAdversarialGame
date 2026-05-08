def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    order = sorted(dirs, key=lambda d: (d[0], d[1]))  # deterministic tie-break

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Choose a primary objective deterministically
    if unclaimed:
        # nearest unclaimed; tie by smaller y then x
        tx, ty = min(unclaimed, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[1], c[0]))
    else:
        # no unclaimed: counterclaim by heading toward opponent territory or opponent position
        target = (ox, oy)
        # if opponent territory exists, target nearest opponent-owned cell
        if opp_terr:
            target = min(opp_terr, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[1], c[0]))
        tx, ty = int(target[0]), int(target[1])

    best = None
    best_score = -10**9
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Heuristic: prefer moving closer to (tx,ty), and especially entering opponent territory.
        dist_to_target = abs(nx - tx) + abs(ny - ty)
        # discourage moving away from opponent when we're not targeting unclaimed
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        score = -dist_to_target

        if (nx, ny) in opp_terr:
            score += 40  # strong counterclaim incentive
        if not unclaimed and opp_terr:
            score += 0.5 * (-dist_to_opp)

        # subtle preference to keep movement non-stagnant unless best
        if dx == 0 and dy == 0:
            score -= 1

        # tie-break by deterministic lexicographic move
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]