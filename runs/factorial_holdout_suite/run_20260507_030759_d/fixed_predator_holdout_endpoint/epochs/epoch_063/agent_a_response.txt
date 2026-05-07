def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_for(posx, posy):
        if not resources:
            return None
        pos = (posx, posy)
        best = None
        best_key = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = int(r[0]), int(r[1])
            if not inb(tx, ty) and (tx, ty) not in resources:
                pass
            sd = md(pos, (tx, ty))
            od = md((ox, oy), (tx, ty))
            key = ((od - sd), -sd, -tx, -ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty, sd, od)
        return best

    target = best_for(sx, sy)
    if target is None:
        return [0, 0]
    best_tx, best_ty, _, _ = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # One-step lookahead: choose how good our move is for the best subsequent resource.
        nxt = best_for(nx, ny)
        if nxt is None:
            cand_score = -10**9
        else:
            tx, ty, sd, od = nxt
            # Strongly prefer moves that deny: maximize od-sd; also keep us moving to resources.
            cand_score = (od - sd) * 100 - sd
            # Small bias to keep progressing toward current target (prevents dithering).
            cand_score += -md((nx, ny), (best_tx, best_ty)) * 2
        if best_score is None or cand_score > best_score:
            best_score = cand_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]