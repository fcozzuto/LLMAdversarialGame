def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Predict opponent nearest-resource choice; avoid it if possible.
    opp_target = min(resources, key=lambda t: (dist(ox, oy, t[0], t[1]), t[0], t[1]))

    def score_for_us(t):
        # Prefer closer, but also slightly prefer tiles that are not the opponent's nearest.
        d = dist(sx, sy, t[0], t[1])
        penalty = 1000 if t == opp_target else 0
        return (d + penalty, t[1], t[0])

    target = min(resources, key=score_for_us)
    tx, ty = target

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Ensure move validity; if blocked, pick best among valid deltas by resulting proximity to target.
    cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    seen = set()
    cand2 = []
    for cd in cand:
        if cd not in seen:
            seen.add(cd)
            cand2.append(cd)
    for mv in moves:
        if mv not in seen:
            cand2.append(mv)

    best = (0, 0)
    best_d = None
    for mdx, mdy in cand2[:]:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        if best_d is None or nd < best_d or (nd == best_d and (mdx, mdy) < best):
            best_d = nd
            best = (mdx, mdy)

    if best_d is None:
        return [0, 0]
    return [best[0], best[1]]