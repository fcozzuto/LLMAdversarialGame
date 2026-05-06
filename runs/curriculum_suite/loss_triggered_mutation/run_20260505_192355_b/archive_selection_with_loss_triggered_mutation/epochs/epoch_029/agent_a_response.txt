def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    turn = int(observation.get("turn_index", 0) or 0)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Deterministically choose best next position by advantage over opponent.
    best = None  # (score, tie)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Prefer taking a resource if adjacent/at it (MD==0), otherwise aim for best "swing".
        immediate = 0
        for (rx, ry) in res:
            if nx == rx and ny == ry:
                immediate += 8

        # Find best target for us after the move; compute advantage vs opponent.
        best_adv = None
        best_self_d = None
        for (rx, ry) in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = (od - sd)  # positive means we are closer
            # Tie-break inside target selection to be deterministic: prefer smaller self distance then lexicographic.
            if best_adv is None or adv > best_adv or (adv == best_adv and (sd < best_self_d or (sd == best_self_d and (rx, ry) < best_target))):
                best_adv = adv
                best_self_d = sd
                best_target = (rx, ry)

        # Encourage reaching resources sooner and discourage moving into being "stolen" (lower opponent advantage).
        score = immediate * 100 + best_adv * 10 - best_self_d
        # Deterministic tie breaker that changes with turn parity to avoid sticking in a tie.
        tie = ((nx + ny + turn) & 1, nx, ny)
        if best is None or score > best[0] or (score == best[0] and tie < best[1]):
            best = (score, tie, dx, dy)

    return [int(best[2]), int(best[3])]