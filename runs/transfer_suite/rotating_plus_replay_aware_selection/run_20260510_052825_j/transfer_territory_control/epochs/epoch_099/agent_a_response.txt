def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cx, cy = w // 2, h // 2
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    un_list = list(unclaimed)
    cur_best = 0
    if un_list:
        cur_best = min(abs(ux - sx) + abs(uy - sy) for ux, uy in un_list)

    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        base = 0
        if (nx, ny) in oppT:
            base += 6
        elif (nx, ny) in unclaimed:
            base += 5
        elif (nx, ny) in selfT:
            base += 2
        else:
            base += 1
        dist = 0
        if un_list:
            dist = min(abs(ux - nx) + abs(uy - ny) for ux, uy in un_list)
            base += max(-6, cur_best - dist)  # prefer reducing distance to unclaimed
        # small bias to move generally toward center to avoid corner trapping
        base += -0.1 * (abs(nx - cx) + abs(ny - cy))
        score = int(base * 10)
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]