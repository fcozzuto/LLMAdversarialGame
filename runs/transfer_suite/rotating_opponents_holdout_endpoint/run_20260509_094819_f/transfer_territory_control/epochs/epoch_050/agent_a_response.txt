def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_list = list(oppT)
    un_list = list(uncla)

    best_dx, best_dy = 0, 0
    best_score = None

    # Prefer: immediate opponent cell capture, then unclaimed expansion, else close toward nearest unclaimed;
    # also avoid increasing distance from our territory to prevent getting stranded on blocked side.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in oppT:
            score += 120000
        if (nx, ny) in uncla:
            score += 8000
        if (nx, ny) in selfT:
            score += 1000

        if un_list:
            d_un = min(abs(nx - ux) + abs(ny - uy) for ux, uy in un_list)
            score += 600 - 40 * d_un
        if opp_list:
            d_opp = min(abs(nx - ox) + abs(ny - oy) for ox, oy in opp_list)
            score += 300 - 25 * d_opp

        # Mild bias to move away from edges only when it hurts: keeps exploration steady.
        score -= (nx == 0 or nx == w - 1) * 5
        score -= (ny == 0 or ny == h - 1) * 5

        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]