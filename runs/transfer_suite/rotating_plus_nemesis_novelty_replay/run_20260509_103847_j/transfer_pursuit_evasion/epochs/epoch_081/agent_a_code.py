def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("evasion" in role)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if sx == ox and sy == oy:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        # Pursuer minimizes distance; evader maximizes it.
        score = -d if is_evader else d
        # Tie-break deterministically by preferring diagonal, then positive dx, then positive dy.
        diag = 1 if dx != 0 and dy != 0 else 0
        tie = (diag, dx, dy)
        if best is None or score > best_score or (score == best_score and tie > best[2]):
            best = (dx, dy, tie)
            best_score = score

    if best is None:
        # If all blocked, stay.
        return [0, 0]
    return [int(best[0]), int(best[1])]