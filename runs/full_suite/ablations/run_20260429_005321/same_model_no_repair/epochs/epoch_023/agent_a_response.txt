def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def pick_target():
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            rd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we are closer to; if tie, prefer closer distance.
            score = (od - rd) * 1000 - rd
            if od <= rd:
                score -= 200  # discourage taking resources opponent can contest immediately
            if best is None or score > best[0]:
                best = (score, (rx, ry), rd, od)
        return best[1] if best else None

    target = pick_target()

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Base: encourage moving toward target (or away from opponent corner if none).
        if target is not None:
            tx, ty = target
            prog = -man(nx, ny, tx, ty)  # larger is better
        else:
            # With no resources: stabilize by increasing distance from opponent.
            prog = man(nx, ny, ox, oy)

        # Risk: avoid letting opponent get closer to us.
        opp_closer = man(ox, oy, nx, ny)
        risk = -opp_closer

        # Small anti-blocking: avoid moves that keep us stationary too long.
        stay_pen = -20 if dx == 0 and dy == 0 else 0

        score = prog * 5 + risk + stay_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]