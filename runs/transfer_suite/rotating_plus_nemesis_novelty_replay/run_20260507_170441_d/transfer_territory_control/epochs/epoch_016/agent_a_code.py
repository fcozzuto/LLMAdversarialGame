def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                blocked.add((x, y))
        except:
            pass

    self_term = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_term = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    targets = list(unclaimed)
    if not targets:
        targets = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]

    def nearest_unclaimed_dist2(x, y):
        best = 10**18
        if targets:
            for tx, ty in targets:
                dx = tx - x
                dy = ty - y
                d = dx * dx + dy * dy
                if d < best:
                    best = d
        return best

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_mv = (0, 0)
    best_sc = -10**30

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sc = 0
        d_op = abs(nx - ox) + abs(ny - oy)

        if (nx, ny) in self_term:
            sc += 20
        elif (nx, ny) in opp_term:
            sc -= 220  # don't walk into opponent land unless it's very useful
            # but capturing their cell is still good if it's close to where we want to go
            sc += max(0, 180 - nearest_unclaimed_dist2(nx, ny) // 6)
        elif (nx, ny) in unclaimed or not targets:
            sc += 260
        else:
            sc += 40

        sc += max(0, 120 - nearest_unclaimed_dist2(nx, ny) // 8)

        # Prefer moves that keep us away from the opponent sweeper pressure
        sc -= (10 + 2 * d_op)  # distance-to-opponent acts as "safety"

        # If we have a clear expansion direction, bias away from opponent and toward center
        center_bias = (3.5 - nx) * (3.5 - nx) + (3.5 - ny) * (3.5 - ny)
        sc += int(60 - center_bias * 2)

        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]