def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    if res:
        best = None
        bestv = -10**18
        for rx, ry in res:
            dme = cheb(sx, sy, rx, ry)
            dob = cheb(ox, oy, rx, ry)
            # If opponent can be closer, deprioritize strongly; otherwise prioritize nearer and less contested.
            v = (dob - dme) * 20 - dme
            if best is None or v > bestv or (v == bestv and dme < best[0]):
                bestv = v
                best = (dme, rx, ry)
        _, tx, ty = best
    else:
        # No visible resources: move toward center while keeping away from opponent.
        tx, ty = (W - 1) / 2.0, (H - 1) / 2.0

    bestm = (0, 0)
    bests = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Greedy toward target with obstacle-safe preference and mild anti-collision/anti-approach.
        dt = cheb(nx, ny, int(tx), int(ty)) if res else cheb(nx, ny, int(tx), int(ty))
        dpos_opp = cheb(nx, ny, ox, oy)
        # Corner-case: prefer moves that don't reduce distance to opponent too much when resources exist.
        contested_pen = 0
        if res:
            dme_next = cheb(nx, ny, tx, ty)
            dob_now = cheb(ox, oy, tx, ty)
            contested_pen = 15 if dme_next >= dob_now else 0
        # Small tie-break to encourage horizontal/vertical progress deterministically
        tb = 0.001 * (0 if dx == 0 else (0.5 if dx > 0 else -0.5)) + 0.0001 * (0 if dy == 0 else (0.5 if dy > 0 else -0.5))
        score = -dt + 0.03 * dpos_opp - contested_pen + tb
        if score > bests:
            bests = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]