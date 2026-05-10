def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) == 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) == 2)
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) == 2]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def adj_to_opp_cell(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    return True
        return False

    # Pick a deterministic target: prioritize unclaimed far from opponent territory edges.
    best = None
    if unclaimed:
        opp_list = list(opp_terr)
        for tx, ty in unclaimed:
            if (tx, ty) in self_terr:
                continue
            # distance to closest opponent territory cell
            mind = 10**9
            for px, py in opp_list[:50]:  # cap for determinism/perf
                d = cheb(tx, ty, px, py)
                if d < mind:
                    mind = d
            if mind == 10**9:
                mind = cheb(tx, ty, ox, oy)
            # discourage adjacency to opponent for edge-claim style opponents
            edge_pen = 6 if adj_to_opp_cell(tx, ty) else 0
            dist_from_me = cheb(sx, sy, tx, ty)
            score = mind - edge_pen - 0.1 * dist_from_me
            if best is None or score > best[0] or (score == best[0] and (tx, ty) < best[1]):
                best = (score, (tx, ty))
    target = best[1] if best else (ox, oy)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            # move quality: closer to target, but keep away from opponent
            dist_to_t = cheb(nx, ny, target[0], target[1])
            if opp_terr:
                mind_opp = 10**9
                for px, py in list(opp_terr)[:50]:
                    d = cheb(nx, ny, px, py)
                    if d < mind_opp:
                        mind_opp = d
            else:
                mind_opp = cheb(nx, ny, ox, oy)
            # If stepping into an opponent cell could flip, still allow if it improves net safety+progress.
            step_adv = 0.0
            if (nx, ny) in opp_terr:
                step_adv -= 1.0  # conservative: avoid entering opponent territory
            # Prefer capturing unclaimed: if target is unclaimed, moving closer helps naturally.
            # Safety margin strongly weighted.
            score = (2.5 * mind_opp) - (1.2 * dist_to_t) + step_adv
            candidates.append((score, dx, dy, (nx, ny)))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]