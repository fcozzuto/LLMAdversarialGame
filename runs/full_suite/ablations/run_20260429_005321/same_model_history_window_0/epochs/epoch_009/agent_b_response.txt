def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    k = 3

    def clamp(x, y):
        if x < 0 or x >= w or y < 0 or y >= h:
            return None
        if (x, y) in obstacles:
            return None
        return (x, y)

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def nearest_targets(pos, n=k):
        ds = sorted(((dist(pos, r), i, r) for i, r in enumerate(resources)), key=lambda t: t[0])
        return [t[2] for t in ds[:min(n, len(ds))]]

    def greedy_next(opos, targets):
        best = None
        best_score = None
        for dx, dy in deltas:
            np = clamp(opos[0] + dx, opos[1] + dy)
            if np is None:
                continue
            md = min(dist(np, t) for t in targets)
            score = -md
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return best if best is not None else (0, 0)

    targets = nearest_targets((sx, sy))
    best_move = (0, 0)
    best_total = None

    for dx, dy in deltas:
        np = clamp(sx + dx, sy + dy)
        if np is None:
            continue
        our_md = min(dist(np, t) for t in targets)
        our_next_targets = nearest_targets(np)
        # simulate opponent greedy towards their nearest resources after we move
        opp_targets = nearest_targets((ox, oy))
        odx, ody = greedy_next((ox, oy), opp_targets)
        nop = clamp(ox + odx, oy + ody)
        if nop is None:
            nop = (ox, oy)
        opp_md = min(dist(nop, t) for t in nearest_targets(nop))
        # contention: discourage moving into squares opponent would also reach quickly
        cont = dist(np, nop)
        # bonus if we move closer to the most "central" nearby resources
        cx = sum(t[0] for t in our_next_targets) / len(our_next_targets)
        cy = sum(t[1] for t in our_next_targets) / len(our_next_targets)
        center_bonus = -dist(np, (cx, cy))
        total = (-our_md) + (opp_md * 0.6) + (cont * -0.15) + (center_bonus * 0.3)
        if best_total is None or total > best_total:
            best_total = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]