def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

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
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Deterministic preference: prioritize resources where we arrive no later than opponent, else chase closest.
    cornerscore = lambda x, y: (x * y, x + y)  # favors central-ish but deterministic

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my = (nx, ny)
        # Evaluate by best achievable advantage among a small deterministic subset of resources.
        # Sort resources deterministically by (my_dist, opp_dist, cornerscore) without heavy search.
        scored = []
        for r in resources:
            md = dist(my, r)
            od = dist((ox, oy), r)
            adv = od - md  # positive means we get there first/earlier
            scored.append((adv, md, od, r[0], r[1]))
        scored.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
        # Consider top K for stability.
        K = 4 if len(scored) >= 4 else len(scored)
        top = scored[:K]

        # Also include "intercept" pressure: prefer moves that reduce distance to the opponent's best target.
        opp_best = min(resources, key=lambda r: (dist((ox, oy), r), dist(my, r), r[0], r[1]))
        inter = dist(my, opp_best) - dist((ox, oy), opp_best)

        # Final heuristic: maximize advantage, then minimize our distance, penalize letting opponent be closer.
        # Small deterministic tie-break by cornerscore of our position.
        adv_sum = sum(t[0] for t in top) * 3
        md_best = top[0][1]
        od_best = top[0][2]
        let_pass = 0
        if od_best < md_best:
            let_pass = (md_best - od_best) * 2
        cs = cornerscore(nx, ny)[0] - cornerscore(sx, sy)[0]
        value = adv_sum - md_best * 2 - let_pass + (-inter) + cs

        if best is None or value > best[0] or (value == best[0] and (dx, dy) < best[1]):
            best = (value, (dx, dy))

    return [best[1][0], best[1][1]]