def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if len(p) >= 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if len(p) >= 2)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    best = [0, 0]
    best_sc = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sc = 0
        # Prefer moving into new territory/unclaimed; prefer center control.
        if (nx, ny) in unclaimed:
            sc += 40
        if (nx, ny) in opp_terr:
            sc += 25  # likely flips on entry, good for edge-claimer archetype
        if (nx, ny) in self_terr:
            sc -= 5  # avoid wasting moves

        sc += -2 * dist((nx, ny), (cx, cy))
        # Contest opponent: prefer reducing distance when attacking, else keep some separation.
        d_before = dist((sx, sy), (ox, oy))
        d_after = dist((nx, ny), (ox, oy))
        if d_after <= d_before:
            sc += 12
        else:
            sc -= 6

        # Discourage stepping toward opponent if it doesn't gain anything.
        if (nx, ny) not in opp_terr and (nx, ny) not in unclaimed:
            sc -= 3 * max(0, d_after - 1)

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best