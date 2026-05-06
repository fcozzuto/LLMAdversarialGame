def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Denier-aware: either contest the resource closest to opponent, or take a resource they can't reach soon.
    opp_nearest = min(res, key=lambda p: (md((ox, oy), p), p[0], p[1]))
    best_target = None
    best_score = -10**9

    for p in res:
        ds = md((sx, sy), p)
        do = md((ox, oy), p)
        # contestability and denial: prefer resources opponent targets, but only if we can arrive no later
        contest = 1 if ds <= do else 0
        # prefer taking what is farthest from opponent, unless we can deny their nearest quickly
        dist_adv = (do - ds)
        near_to_opp = -md((ox, oy), p)
        score = contest * (200 + dist_adv * 10) + (not contest) * (dist_adv * 2 + near_to_opp * 0.5)

        # explicit bias toward opponent-nearest resource to disrupt deniers
        if p == opp_nearest:
            score += 60

        # deterministic tie-breaker
        if score > best_score or (score == best_score and (p[0], p[1]) < (best_target[0], best_target[1]) if best_target else True):
            best_score = score
            best_target = p

    tx, ty = best_target
    # Choose best immediate move toward target, but avoid stepping into obstacles/outside.
    best_move = (0, 0)
    best_mscore = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        ns = md((nx, ny), (tx, ty))
        no = md((nx, ny), (ox, oy))  # moving away can slow denier routes
        # objective: reduce distance to target; if contesting, also slightly increase distance from opponent
        ds = md((sx, sy), (tx, ty))
        do = md((ox, oy), (tx, ty))
        contest = 1 if ds <= do else 0
        mscore = (-ns) + contest * (no * 0.1)
        if mscore > best_mscore or (mscore == best_mscore and (dx, dy) < best_move):
            best_mscore = mscore
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]