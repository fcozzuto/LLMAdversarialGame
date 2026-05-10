def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    self_role = observation.get("self_role") or "pursuer"
    opp_role = observation.get("opponent_role") or "evader"

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def legal_moves(x, y):
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                out.append((dx, dy, nx, ny))
        return out if out else [(0, 0, x, y)]

    # Predict opponent next move against our current position (deterministic).
    opp_moves = legal_moves(ox, oy)
    best_opp = None
    for dx, dy, nx, ny in opp_moves:
        v = dist2(nx, ny, sx, sy)
        # evader maximizes distance; pursuer minimizes distance
        score = v if opp_role == "evader" else -v
        cand = (score, dx, dy, nx, ny)
        if best_opp is None or cand > best_opp:
            best_opp = cand
    _, _, _, pred_ox, pred_oy = best_opp

    # Evaluate our move against predicted opponent.
    my_moves = legal_moves(sx, sy)
    best_my = None
    for dx, dy, nx, ny in my_moves:
        d = dist2(nx, ny, pred_ox, pred_oy)
        score = d if self_role == "evader" else -d
        # tie-break: deterministic lexicographic preference on (score, dx, dy)
        cand = (score, dx, dy, nx, ny)
        if best_my is None or cand > best_my:
            best_my = cand

    _, dx, dy, _, _ = best_my
    return [int(dx), int(dy)]