def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    rpos = []
    for r in resources:
        q = rep(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a current target with deterministic "advantage" logic.
    best_t = None
    best_key = None
    for tx, ty in rpos:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        adv = od - sd
        # If we are behind, still prefer the resource that flips advantage soon (smaller od).
        key = (adv, -od, -sd) if adv >= 0 else (adv, -sd, -od)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Score each possible next move against the chosen target, with a penalty for making opponent closer.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nsd = abs(tx - nx) + abs(ty - ny)
        nod = abs(tx - ox) + abs(ty - oy)
        # Encourage reducing our distance and ensuring we remain closer than opponent.
        score = 200 * (nod - nsd) - 3 * nsd
        # If our move brings us onto a resource sooner, boost strongly.
        if (nx, ny) in rpos:
            score += 500
        # Small tie-break toward staying aligned with the target direction.
        score += - (abs(tx - nx) + abs(ty - ny) + abs(dx) + abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move