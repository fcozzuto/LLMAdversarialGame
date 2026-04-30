def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If no resources, run to center-ish to reduce travel distance variance.
    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = (md(nx, ny, cx, cy), nx, ny)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Otherwise, pick move that maximizes resource "advantage" vs opponent.
    # advantage = (opponent distance - our distance); higher means we can reach first.
    # Also lightly penalize being farther and moving into opponent's likely reach.
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        our_to = min(md(nx, ny, rx, ry) for (rx, ry) in resources)
        opp_to = min(md(ox, oy, rx, ry) for (rx, ry) in resources)

        # Best advantage achievable from this next position over all resources.
        # Break ties deterministically by closer our_to then lexicographic target.
        best_adv = None
        best_tx, best_ty = None, None
        for (rx, ry) in resources:
            da = md(nx, ny, rx, ry)
            db = md(ox, oy, rx, ry)
            adv = db - da
            if best_adv is None or (adv, -da, rx, ry) > (best_adv, -md(nx, ny, best_tx, best_ty), best_tx, best_ty):
                best_adv = adv
                best_tx, best_ty = rx, ry

        # Opponent next-turn pressure: if opponent can also move closer to our chosen target.
        opp_next_min = md(ox, oy, best_tx, best_ty)
        # simulate opponent one step to reduce to min distance (still deterministic, 9 moves).
        nd = opp_next_min
        for odx, ody in deltas:
            tx, ty = ox + odx, oy + ody
            if inb(tx, ty) and (tx, ty) not in obstacles:
                nd = min(nd, md(tx, ty, best_tx, best_ty))

        # Score: prioritize advantage, then proximity to target, then slight avoidance of being contested.
        score = best_adv * 5 - our_to * 1.2 - max(0, nd - opp_next_min) * 0.1 - abs(nx - sx) * 0.01

        if best_score is None or (score, -our_to, nx, ny) > (best_score, -our_to, best[2] if False else 0, 0):
            # tie-break deterministically using target then coordinates
            best_score = score
            best = (dx, dy, nx, ny)

    return [int(best[0]), int(best[1])]