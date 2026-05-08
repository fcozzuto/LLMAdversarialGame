def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if unclaimed:
        opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
        # Counterclaim archetype: prefer far-from-opponent unclaimed to reduce easy flips back.
        # If none, fall back to nearest-from-opponent boundary-like targets.
        candidates = []
        for x, y in unclaimed:
            x, y = int(x), int(y)
            if not inb(x, y):
                continue
            d_opp = man(ox, oy, x, y)
            d_self = man(sx, sy, x, y)
            near_opp = 1 if any((x + dx, y + dy) in opp_t for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy) else 0
            # Primary: maximize distance from opponent; Secondary: minimize self distance; Tertiary: deterministic cell id.
            candidates.append((d_opp, -near_opp, -d_self, x, y))
        if candidates:
            candidates.sort(reverse=True)
            tx, ty = candidates[0][3], candidates[0][4]
        else:
            tx, ty = sx, sy
    else:
        # If no unclaimed, keep pressure by moving toward opponent but avoid immediate obstacle
        tx, ty = ox, oy

    best = (None, None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate the next step toward the target.
        d1 = man(nx, ny, tx, ty)
        d2 = man(nx, ny, ox, oy)
        # Also slightly avoid stepping into our already claimed territory edges too aggressively.
        # (Deterministic tie-break via coordinates.)
        bonus_self = 1 if (nx, ny) in self_t else 0
        score = (-(d1), d2, bonus_self, nx, ny)
        if best[0] is None or score > best:
            best = score
    nx, ny = (sx, sy) if best[0] is None else (best[3], best[4])
    return [nx - sx, ny - sy]