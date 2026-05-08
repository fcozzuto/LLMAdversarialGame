def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)
    unclaimed_list = list(unclaimed)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        gain = 0
        if (nx, ny) in opp_t:
            gain += 8
        elif (nx, ny) in unclaimed:
            gain += 3
        elif (nx, ny) in self_t:
            gain += 0
        else:
            gain += 1 if (nx, ny) not in opp_t else 0

        if unclaimed_list:
            md = 10**9
            for tx, ty in unclaimed_list:
                d = abs(tx - nx) + abs(ty - ny)
                if d < md:
                    md = d
            gain -= 0.35 * md

        # Starve opponent by prioritizing moves that reduce distance to their frontier cells
        if opp_t:
            bd = 10**9
            for px, py in opp_t:
                d = abs(px - nx) + abs(py - ny)
                if d < bd:
                    bd = d
            gain -= 0.08 * bd

        # Mild preference to advance generally toward opponent to enable flips
        gain -= 0.03 * (abs(ox - nx) + abs(oy - ny))
        # Tie-break deterministically
        candidates.append((gain, abs(dx), abs(dy), dx, dy, nx, ny))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, _, _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]