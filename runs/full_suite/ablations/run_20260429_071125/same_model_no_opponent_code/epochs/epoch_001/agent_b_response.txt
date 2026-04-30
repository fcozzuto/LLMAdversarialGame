def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # fallback: head to center while avoiding obstacles
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in resources:
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            # prefer resources where we are closer; break ties by absolute distance
            score = (sd - od, sd, abs(rx - (w - 1 - ox)) + abs(ry - (h - 1 - oy)))
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                dist = abs(tx - nx) + abs(ty - ny)
                towards = (dx == 0 or (tx - sx) * dx > 0) or (dx == 0)
                moves.append((dist, abs(tx - nx) + abs(ty - ny), -towards, -abs(tx - nx), -abs(ty - ny), dx, dy))
    if not moves:
        return [0, 0]

    moves.sort()
    return [int(moves[0][5]), int(moves[0][6])]