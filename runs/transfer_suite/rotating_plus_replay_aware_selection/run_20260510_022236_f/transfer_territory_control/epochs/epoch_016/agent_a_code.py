def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        x, y = int(p[0]), int(p[1])
        if ok(x, y):
            targets.append((x, y))
        if len(targets) >= 20:
            break

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Prefer unclaimed near self, far from opponent
        if targets:
            ts = []
            for tx, ty in targets:
                ds = man(nx, ny, sx, sy)  # small tie-break
                du = man(nx, ny, tx, ty)
                do = man(nx, ny, ox, oy)
                # Higher score: closer to target, farther from opponent
                ts.append((-(du) + 0.3 * do - 0.01 * ds, tx, ty))
            ts.sort()
            score = ts[0][0]
        else:
            score = 0.1 * man(nx, ny, ox, oy)  # just run away / stay safe

        # Small deterministic bias to reduce oscillation: don't move toward being adjacent to opponent
        if man(nx, ny, ox, oy) <= 1:
            score -= 5

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]